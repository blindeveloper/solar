**Project setup**

1. run `docker-compose build --no-cache`
2. run `docker-compose up`
3. go to `http://0.0.0.0:8000/docs` to test API. Testing API with this web page docs is super handy.

**Description**
I've decided do go with Python on backend because of use of the fasApi library.
I total there are 5 tables created: Product, System, CustomerOrder, Stock and Email.
For testing API I would go in this order:

1. Add emails, which you want to use for notifications about low stock. `POST: /email`

```
curl -X 'POST' \
  'http://0.0.0.0:8000/email' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "<email@gmail.com>"
}'
```

2. Add new Product. Adding product with same name multiple times will trigger error. `POST /product`

```
curl -X 'POST' \
  'http://0.0.0.0:8000/product' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Inverter"
}'
```

3. Every product creation will trigger Stock update with this product and default stock values.
4. Check if stock was updated using `GET: /stock`

```
curl -X 'GET' \
  'http://0.0.0.0:8000/stock' \
  -H 'accept: application/json'
```

5. Update stock of the created product `PUT: /stock/<product_id>`

```
curl -X 'PUT' \
  'http://0.0.0.0:8000/stock/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "remaining_amount": 100,
  "total_amount": 100
}'
```

6. Create system, every system is set of the products. `POST /system`. System will be created only if products are valid.

```
curl -X 'POST' \
  'http://0.0.0.0:8000/system' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "system": [
    {
      "id": 1,
      "amount": 12
    },
    {
      "id": 2,
      "amount": 20
    },
  ]
}'
```

7. Check id system was created `GET /system`

```
curl -X 'GET' \
  'http://0.0.0.0:8000/system' \
  -H 'accept: application/json'
```

7. Make order. You can order system and/or product at the same time. Product and system IDs should be valid.
   `POST: /order` Every order will be checked after and in case if Store is low, you will get email with product name in it. Ordering low stock product will not trigger email send until stock of this product will be updated.
   In my case all the emails were in spam/junk folder.

```
curl -X 'POST' \
  'http://0.0.0.0:8000/order' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "products": [
    {
      "id": 1,
      "amount": 2
    }
  ],
  "systems": [
    {
      "id": 1692053315593,
      "amount": 1
    }
  ]
}'
```

8. Check storage again, you will see that it's changed because of previous order.
9. tests TBD
