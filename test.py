import os


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "new_blog.settings")

    import django
    django.setup()
    from app01 import models
    # objs =models.Category.objects.extra(select={"num":"select 2 from app01_category where nid =1 "})
    # objs =models.Category.objects.extra(where=["nid>3","nid<6"])
    # for obj in objs:
    #     print(obj.__dict__)



    # cags =models.Category.objects.raw("select * from app01_blog")
    # for cag in cags:
    #     print(cag.__dict__)

    from django.db import connection, connections

    cursor = connection.cursor()  # cursor = connections['default'].cursor()
    cursor.execute("SELECT * from app01_category where nid in (1,2,3)", )
    row = cursor.fetchall()  # fetchall()/fetchmany(..)
    print(row)












