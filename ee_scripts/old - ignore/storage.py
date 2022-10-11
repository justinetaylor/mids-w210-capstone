from pyspark.sql import SparkSession
from pyspark.sql.types import *
from datetime import date

"""
Bare bones storage class. 
This storage class has one table with one schema.
I think this is all we need. We dont need anything complex.

Usage:
import DataStore from storage
storage_client = DataStore()
storage_client.insert_data([[ 'Alameda', '2016', 'County', 0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
"""

class DataStore:
    # class variables

    ##create a spark dataFrame 
    schema = StructType([
        # name, type, nullable
        StructField('Name', StringType(), False),
        StructField('Year', IntegerType(), False),
        StructField('GeometryType', StringType(), False),
        StructField('TreeAreaGained', IntegerType(), False)
        StructField('TreeAreaLost', IntegerType(), False)
        StructField('GrassAreaGained', IntegerType(), False)
        StructField('GrassAreaLost', IntegerType(), False)
        StructField('ShrubAreaGained', IntegerType(), False)
        StructField('ShrubAreaLost', IntegerType(), False)
        StructField('FloodedVegAreaGained', IntegerType(), False)
        StructField('FloodedVegAreaLost', IntegerType(), False)
        StructField('CropsAreaGained', IntegerType(), False)
        StructField('CropsAreaLost', IntegerType(), False)
        StructField('GppLostSummer', LongType(), False)
        StructField('GppGainedWinter', LongType(), False)
        StructField('GppLostSpring', LongType(), False)
        StructField('GppGainedFall', LongType(), False)
    ])

    # methods 

    ## init method or constructor
    def __init__(self):
         self.spark = SparkSession.builder.appName('test').getOrCreate()


    ## insert data
    def insert_data(self, data):
        """
        insert data into the table 
        data: list of lists. must match schema
        """
        pre_computed_data = spark.createDataFrame(data, schema)

        # Create a table on the Databricks cluster and then fill
        # the table with the DataFrame's contents.
        # If the table already exists from a previous run,
        # delete it first.
        spark.sql('USE default')
        spark.sql('DROP TABLE IF EXISTS test_table')
        pre_computed_data.write.saveAsTable('test_table')

        # Query the table on the Databricks cluster, returning rows
        df = spark.sql("SELECT * FROM pre_computed_data " \
            "WHERE (Year == 2016 OR Year == 2017) AND Name == 'Alameda' AND GeometryType == 'COUNTY'")
        df.show()

        # Clean up by deleting the table from the Databricks cluster.
        spark.sql('DROP TABLE test_table')


