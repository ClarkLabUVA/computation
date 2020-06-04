sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)

####################
#
# python3 output_location input1 input2 ....
#
# Input files locations are passed in as command line arguments
#
# First argument is output folder to write to
#
# All arguments after are input locations
#
####################

# Outputs must be written to given folder in order mint ids
# Output folder is given as first command line argument
output_folder = sys.argv[1]

#Computation Passes Input files locations as 3rd argument on
files = sys.argv[2:]

df = sqlContext.read.format("com.databricks.spark.csv")
        .option("header", "false").load(files)

@pandas_udf(schema, PandasUDFType.GROUPED_MAP)
def example(pdf):
    pdf['column2'] = pdf['column1'] * 2
    return pdf

result = df.groupby('id').apply(example)

result.write.save(sys.argv[1],  format='csv')
