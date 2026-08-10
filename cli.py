import csv
import click

from flask.cli import with_appcontext

from app.extensions import db

from app.models.user import User
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.activity import Activity


# Seed Command
@click.command("seed")
@with_appcontext
def seed():
    if User.query.first():
        click.echo("Database already contains data.")
        return

    user = User(
        name="Demo User",
        email="demo@example.com"
    )
    user.set_password("password123")

    db.session.add(user)
    db.session.commit()

    contacts = []
    for i in range(1, 11):
        c = Contact(
            user_id=user.id,
            name=f"Customer {i}",
            email=f"customer{i}@example.com",
            phone=f"555-100{i}",
            company=f"Company {i}",
            notes="Demo Contact"
        )
        db.session.add(c)
        contacts.append(c)

    db.session.commit()

    for c in contacts:
        deal = Deal(
            user_id=user.id,
            contact_id=c.id,
            title=f"{c.company} Renewal",
            value=1000 * c.id,
            status="Open",
            notes="Seeded Deal"
        )
        db.session.add(deal)

    db.session.commit()
    click.echo("Demo data created.")


# CSV Import Command
@click.command("import-contacts")
@click.argument("filename")
@with_appcontext
def import_contacts(filename):
    user = User.query.first()

    if not user:
        click.echo("Create a user first.")
        return

    try:
        with open(filename, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            required = {"name"}

            for row in reader:
                if not required.issubset(row.keys()):
                    click.echo(f"Skipping row, missing 'name': {row}")
                    continue

                contact = Contact(
                    user_id=user.id,
                    name=row["name"].strip(),
                    email=row.get("email", "").strip() or None,
                    phone=row.get("phone", "").strip() or None,
                    company=row.get("company", "").strip() or None,
                    notes=row.get("notes", "").strip() or None
                )
                db.session.add(contact)

        db.session.commit()
        click.echo("Import completed.")
    except FileNotFoundError:
        click.echo(f"File not found: {filename}")
    except Exception as e:
        click.echo(f"Import failed: {e}")
