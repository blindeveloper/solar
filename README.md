**Project setup**

1. run `docker-compose build --no-cache`
2. run `docker-compose up`
3. go to `http://0.0.0.0:8000/docs` to test API

**API explanation**

1. To add new product use: `POST: /product`

```
curl -X 'POST' \
  'http://0.0.0.0:8000/product' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Optimizer",
  "amount": 500
}'
```

2. To get list of all created products use `GET: /product`

```
curl -X 'GET' \
  'http://0.0.0.0:8000/product' \
  -H 'accept: application/json'
```

3. To create new system use `POST: /system`

```
curl -X 'POST' \
  'http://0.0.0.0:8000/system' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "system": [
    {
      "id": 1,
      "amount": 22
    }
  ]
}'
```

4. To get list of all created systems use `GET: `

```
curl -X 'GET' \
  'http://0.0.0.0:8000/system' \
  -H 'accept: application/json'
```

5. To change amount of product stock use `PUT: product/{product_id}`

```
curl -X 'PUT' \
  'http://0.0.0.0:8000/product/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 500
}'
```

6. To make order use `POST: /order`

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
      "id": 1691930907636,
      "amount": 2
    }
  ]
}'
```

**Tasks**

- check availability amount on order validation
- email functionality
- tests

**DONE**

- handle new order with system
- handle new product with random set of products
- create order model
- update product with new stock
- create system model
- add product
- add to stock function
- seeding the database with products
