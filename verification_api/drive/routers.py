class driveRouter(object):

    def db_for_read(self, model, **hints):

        if model._meta.app_label == 'drive':
            return 'drive'
        return None

    def db_for_write(self, model, **hints):

        if model._meta.app_label == 'drive':
            return 'drive'
        return None

    def allow_syncdb(self, db, model):

        if db == 'drive':
            return model._meta.app_label == 'drive'
        elif model._meta.app_label == 'drive':
            return False
        return None


#
# class drivelogRouter(object):
#
#     def db_for_read(self, model, **hints):
#
#         if model._meta.app_label == 'drivelog':
#             return 'drivelog'
#         return None
#
#     def db_for_write(self, model, **hints):
#
#         if model._meta.app_label == 'drivelog':
#             return 'drivelog'
#         return None
#
#     def allow_syncdb(self, db, model):
#
#         if db == 'drivelog':
#             return model._meta.app_label == 'drivelog'
#         elif model._meta.app_label == 'drivelog':
#             return False
#         return None