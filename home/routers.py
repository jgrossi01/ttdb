class HarnessRouter:
    def db_for_read(self, model, **hints):
        """Usar harness para leer modelos de models_harness"""
        if model._meta.app_label == "home":  # Cambia 'home' si es otra app
            return "harness"
        return None

    def db_for_write(self, model, **hints):
        """Usar harness para escribir modelos de models_harness"""
        if model._meta.app_label == "home":
            return "harness"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Evita que Django intente crear/modificar tablas en harness"""
        if db == "harness":
            return False
        return None
