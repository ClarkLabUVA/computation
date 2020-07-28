import os

INPUTS = os.environ.get('DATA')
OUTPUT_FOLDER = os.environ.get('OUTPUT')


MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')
OUTPUT = os.environ.get('OUTPUT')

minioClient = Minio(MINIO_URL,
                  access_key=MINIO_ACCESS_KEY,
                  secret_key=MINIO_SECRET,
                  secure=False)

bucket = OUTPUT.split('/')[2]
rest = '/'.join(OUTPUT.split('/')[3:])

def upload(file,name):
    with open(file, 'rb') as file_data:
        file_stat = os.stat(file)
        minioClient.put_object(bucket, rest + '/' + name,
                               file_data, file_stat.st_size)

def get_distribution(id):
    """Validates that given identifier exists in Mongo.
        Returns location in minio. """
    if isinstance(id,list):
        locations = []
        names = []
        for i in id:
            location, name = get_distribution(i)
            if location == '':
                continue
            locations.append(location)
            names.append(name)
        return locations, names
    r = requests.get(ORS_URL + id)
    if r.status_code != 200:
        print(ORS_URL + id)
        return False, "Identifier Doesn't Exist."
    try:
        data_dict = r.json()
        data_url = data_dict['distribution'][0]['contentUrl']
        file_location = '/'.join(data_url.split('/')[1:])
        name = data_dict['name']
    except:
        return '',''
    return file_location, name

def read_in_data(sqlContext,format = "com.databricks.spark.csv",header = "true"):
    files = INPUTS.split(',')
    df = sqlContext.read.format(format).option("header", header).load(files)
    return df

def download_data(locations,names):
    file_location = []
    for i in range(len(locations)):
        bucket = locations[i].split('/')[0]
        rest = "/".join(locations[i].split('/')[1:])
        data = minioClient.get_object(bucket, rest)
        file_location.append('/data/' + rest.split('/')[-1])
        with open('/data/' + rest.split('/')[-1], 'wb') as file_data:
            for d in data.stream(32*1024):
                file_data.write(d)
    return file_location

def download_local(ids):
    location, name = get_distribution(id)
    file_locations = download_data(location,name)
    return file_locations

def write_data(result,format = 'csv'):
    if isinstance(result,str):
        path = result
        for root, dirs, files in os.walk(path):
            for name in files:
                file_loc = root + '/' + name
                upload(file_loc,name)
    else:
        result.write.save(OUTPUT_FOLDER,  format='csv')
