from pyspark import SparkContext, SQLContext
import sys
sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)


df = sqlContext.read.format("com.databricks.spark.csv").option("header", "false").load(sys.argv[2])


import numpy as np
import pandas as pd
from pyspark.sql.functions import *
from pyspark.sql.types import *

def CO_tc3(y,tau = 'ac'):

    if tau == 'ac':

        tau = CO_FirstZero(y,'ac')

    # else:
    #
    #     tau = CO_FirstMin(y,'mi')

    N = len(y)

    yn = y[0:N-2*tau]
    yn1 = y[tau:N-tau]
    yn2 = y[tau*2:N]

    raw = np.mean(np.multiply(np.multiply(yn,yn1),yn2)) / (np.absolute(np.mean(np.multiply(yn,yn1))) ** (3/2))

    outDict = {}

    outDict['raw'] = raw

    outDict['abs'] = np.absolute(raw)

    outDict['num'] = np.mean(np.multiply(yn,np.multiply(yn1,yn2)))

    outDict['absnum'] = np.absolute(outDict['num'])

    outDict['denom'] = np.absolute( np.mean(np.multiply(yn,yn1)))**(3/2)

    return outDict

def parse_outputs(outputs,results,func):
    for key in outputs:
        if isinstance(outputs[key],list) or isinstance(outputs[key],np.ndarray):
            i = 1
            for out in outputs[key]:
                results[(func + '_' + key + ' _' + str(i))] = out
                i = i + 1
        else:
            results[(func + '_' + key)] = outputs[key]
    return results


schema = StructType([
  StructField("CO_tc3_50__raw", FloatType()),
  StructField("CO_tc3_50__abs", FloatType()),
  StructField("CO_tc3_50__num", FloatType()),
  StructField("CO_tc3_50__absnum", FloatType()),
  StructField("CO_tc3_50__denom", FloatType()),
  StructField("time", StringType()),
  StructField("id", StringType())
])

df = df.withColumn("id2", monotonically_increasing_id())

@pandas_udf(schema, PandasUDFType.GROUPED_MAP)
def round3(pdf):
    y = pdf.values[0][:-3].astype('float')
    results = {}
    out = CO_tc3(y,50)
    results = parse_outputs(out,results,'CO_tc3_' + str(50) + '_')
    df = pd.DataFrame([results])
    df['time'] = str(pdf.values[0][-3])
    df['id'] = str(pdf.values[0][-2])
    return df

result = df.groupby('id2').apply(round3)

result.coalesce(1).write.save(sys.argv[1],  format='csv')
