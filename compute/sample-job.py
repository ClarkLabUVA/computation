#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
