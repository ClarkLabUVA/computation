# Compute API Documentation 

The compute service handles running of 

# Endpoints
 - **/job**
 - **/nypipe**
 - **/spark**

# /job

Handles tracking running jobs and creating jobs with arbitrary containers. 

## GET

List all running jobs. 
```console
$ curl http://clarklab.uvarc.io/compute/job 
```

## POST

Starts a new job computing the given script on the requested data. 

### Parameters 

 - **datasetID**
 - **scriptID**
 - **containerID**


```bash
$ curl --request POST \
  --url https://clarklab.uvarc.io/job \
  --header 'Authorization: Bearer YOUR_JWT' \
  --header 'Content-Type: application/json' \
  --data '{"datasetID":"ark:99999/data", "scriptID": "ark:99999/script", "containerID":"ark:99999/dockerID"}'
```

# /nypipe

Handles tracking running jobs and creating jobs with custom nipype container for tracking detailed provenance. 

## POST

Starts a new job computing the given script on the requested data. 

### Parameters 

 - **datasetID**
 - **scriptID**

```bash
$ curl --request POST \
  --url https://clarklab.uvarc.io/nypipe \
  --header 'Authorization: Bearer YOUR_JWT' \
  --header 'Content-Type: application/json' \
  --data '{"datasetID":"ark:99999/data", "scriptID": "ark:99999/script"}'
```

# /spark

Handles tracking running jobs and creating spark jobs. 

## POST

Starts a new job computing the given script on the requested data. 

### Parameters 

 - **datasetID**
 - **scriptID**

```bash
$ curl --request POST \
  --url https://clarklab.uvarc.io/spark \
  --header 'Authorization: Bearer YOUR_JWT' \
  --header 'Content-Type: application/json' \
  --data '{"datasetID":"ark:99999/data", "scriptID": "ark:99999/script"}'
```
