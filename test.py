import os


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "new_blog.settings")

    import django
    django.setup()
    from app01 import models
    article = models.Article.objects.filter(nid=1).first()
    article_detail = models.ArticleDetail.objects.filter(article=article).first()
    print(article_detail.content)
