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

def read_in_data(sqlContext,format = "com.databricks.spark.csv",header = "true"):
    files = INPUTS.split(',')
    df = sqlContext.read.format(format).option("header", header).load(files)
    return df


def write_data(result,format = 'csv'):
    if isinstance(result,str):
        path = result
        for root, dirs, files in os.walk(path):
            for name in files:
                file_loc = root + '/' + name
                upload(file_loc,name)
    else:
        result.write.save(OUTPUT_FOLDER,  format='csv')
