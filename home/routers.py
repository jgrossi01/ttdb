class HarnessRouter:
    MODELOS_HARNESS = {"conexiones"}  # Lista de modelos que deben ir en "harness"

    def db_for_read(self, model, **hints):
        """Usar harness para leer modelos específicos"""
        if model._meta.model_name in self.MODELOS_HARNESS:
            return "harness"
        return "default"

    def db_for_write(self, model, **hints):
        """Evita escritura en harness, todo lo demás usa default"""
        if model._meta.model_name in self.MODELOS_HARNESS:
            return "harness"
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Evita migraciones en harness"""
        if db == "harness":
            return False
        return True  # Permite migraciones en default
