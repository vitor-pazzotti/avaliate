import org.apache.spark.sql.functions.udf
import org.apache.spark.sql.SparkSession
import spark.implicits._
import org.apache.spark.sql.functions._
import org.apache.spark.sql.Row
import java.text.SimpleDateFormat
import org.joda.time.Days
import org.apache.spark.sql.types.{DateType, IntegerType, DoubleType}
import java.util.{Calendar, Date}


object processamento_spark
{
    def main(args: Array[String])
    {
        val spark = SparkSession.builder.appName("processamento_spark").getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        import spark.implicits._

        val dolar = spark.read.format("csv").option("header", "true").csv("hdfs://localhost:8020/user/vitorPazzotti/input/dolar_data.csv");
        val crypto = spark.read.format("csv").option("header", "true").csv("hdfs://localhost:8020/user/vitorPazzotti/input/crypto_data.csv");
        
        val calender = Calendar.getInstance()
        calender.roll(Calendar.DAY_OF_YEAR, -1)
        val date_format = new SimpleDateFormat("d-M-y")
        val day = date_format.format(calender.getTime())

        val convertCryptoToReal : (Float, Float) => Float = (crypto:Float, usd_brl:Float) => {crypto * usd_brl};
        
        val df1 = spark.sql("SELECT Cotacao as cotacao from dolarTemp")
        val df2 = spark.sql("SELECT Data as data from dolarTemp")

        val cross = df2.crossJoin(df1)
        val tabelaDolar = cross.select(cross("cotacao").cast(DoubleType).as("cotacao"),cross("data").cast(DateType).as("data"))
        val convertCryptoToRealUDF = udf(convertCryptoToReal);

        val result = dolar_crypto.withColumn("priceReal",convertCryptoToRealUDF(dolar_crypto.col("priceUSD"),dolar_crypto.col("value")));
        
        val final_output = result.select("code", "symbol", "name", "priceUSD", "priceReal", "priceBTC", "change24H", "volume24H", "timestamp");
        
        val filename = final_output.select("timestamp").as[String].first()
        val file_default = "hdfs://localhost:8020/user/vitorPazzotti/output/" + filename + ".json"
        val file_transferidos = "hdfs://localhost:8020/user/vitorPazzotti/output/transferidos/" + filename + ".json"
        
        final_output.write.json(file_default)




//         ///////////////////////////////

// val dolar = spark.read.option("header","true").csv("home/semantix/Avaliacao/vitor-avaliacao/vitorPazzotti/*.csv")
// val crypto = spark.read.option("header","true").csv("user/vitorPazzotti/*.csv")

// dolar.createOrReplaceTempView("dolarTemp")
// val calender = Calendar.getInstance()
// calender.roll(Calendar.DAY_OF_YEAR, -1)
// val date_format = new SimpleDateFormat("d-M-y")
// val day = date_format.format(calender.getTime())


// val df1 = spark.sql("SELECT Cotacao as cotacao from dolarTemp")
// val df2 = spark.sql("SELECT Data as data from dolarTemp")

// val cross = df2.crossJoin(df1)
// val tabelaDolar = cross.select(cross("cotacao").cast(DoubleType).as("cotacao"),cross("data").cast(DateType).as("data"))
// val tabelaMoeda = crypto.select(crypto("code"),crypto("name"),crypto("symbol"),crypto("change24H"),crypto("volume24H"),crypto("priceBTC"),crypto("timestamp"),crypto("priceUSD").cast(DoubleType).as("priceUSD"))
// val crossJoin = tabelaMoeda.crossJoin(tabelaDolar)
// crossJoin.createOrReplaceTempView("crossTemp")
// val df_final = spark.sql("SELECT code,name,symbol,change24H,volume24H,priceBTC,priceUSD,CAST(priceUSD * cotacao AS DECIMAL(10,2)) as PriceReal,timestamp,data from crossTemp")