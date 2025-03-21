class DB2Router:
    def db_for_read(self, model, **hints):
        """Usar db2 para leer modelos de models_db2"""
        if model._meta.app_label == "home":  # Cambia 'home' si es otra app
            return "db2"
        return None

    def db_for_write(self, model, **hints):
        """Usar db2 para escribir modelos de models_db2"""
        if model._meta.app_label == "home":
            return "db2"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Evita que Django intente crear/modificar tablas en db2"""
        if db == "db2":
            return False
        return None
