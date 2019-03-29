from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .apiLists import grlst,mkdir,rcpy,rdel,rmv,rshr,rupld,rshrcc,rshrma,rshrmd

urlpatterns = format_suffix_patterns([
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('grlst/', grlst.get_resource_list),
    path('mkdir/', mkdir.make_directory),
    path('rcpy/',rcpy.resource_copy),
    path('rdel/',rdel.resource_delete),
    path('rmv/',rmv.resource_move),
    path('rshr/',rshr.resource_share),
    path('rupld/',rupld.resource_upload),
    path('rshrcc/',rshrcc.resource_share_cancel),
    path('rshrma/',rshrma.resource_share_member_add),
    path('rshrmd/',rshrmd.resource_share_member_delete),
])