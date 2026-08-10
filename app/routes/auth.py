@@
-    token = create_access_token(identity=user.id)
+    # Ensure 'sub' (subject) claim is a string to satisfy JWT validation
+    token = create_access_token(identity=str(user.id))
@@
-    token = create_access_token(identity=user.id)
+    # Ensure 'sub' (subject) claim is a string to satisfy JWT validation
+    token = create_access_token(identity=str(user.id))
@@
-def me():
-    uid = get_jwt_identity()
-    user = User.query.get_or_404(uid)
-    return jsonify(user.to_dict())
+def me():
+    # JWT identity is stored as a string; convert back to int for DB lookups
+    uid = int(get_jwt_identity())
+    user = User.query.get_or_404(uid)
+    return jsonify(user.to_dict())
