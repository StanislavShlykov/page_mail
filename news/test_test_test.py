from .models import Category

cat1 = Category(cat_name = 'Политика')
cat2 = Category(cat_name = 'История')
for i in cat1.users:
    print(i)