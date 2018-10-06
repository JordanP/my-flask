# my-flask

## Build
With docker:
```bash
docker build -t myflask:latest .
```

## Run
With docker:
```bash
docker run --name myflask -d -p 5000:5000 --rm myflask:latest
```

With Tox
```bash
tox -e run
```

## Test
Functionnal + coverage test
```bash
tox -e cover
```

A-la-mano
```bash
curl -A Arachni/v1.2.1 http://127.0.0.1:5000/
curl -H "X-Sqreen-Integrity: 17f9ba1af1646521d786943433ddb35415ae2cc40182e9196f1502af1567a257" --data-binary '[{"sqreen_payload_type": "security_event", "date_occurred": "2018-10-10T08:32:25.169232+00:00"}]' -H "content-type: application/json" http://127.0.0.1:5000/
```

## API
This app has a single route `'/'` that should be the target for the Webhook.