# This R script will read in the spatial grid and covariates,
# perform some processing steps, produce the SOC prediction 
# and variance prediction, and write them to disk.

install.packages('data.table')
install.packages('randomForest')
install.packages('raster')
library(data.table)
library(randomForest)
library(raster)

covariates <- fread('grid.csv')
cc <- covariates[complete.cases(covariates),]

#reduce the number of factors in ncdl
cc$ncdl <- as.factor(cc$ncdl)

#urban areas
levels(cc$ncdl)[levels(cc$ncdl)=="122"] <- "121"
levels(cc$ncdl)[levels(cc$ncdl)=="123"] <- "121"
levels(cc$ncdl)[levels(cc$ncdl)=="124"] <- "121"

#tree crops
levels(cc$ncdl)[levels(cc$ncdl)=="218"] <- "71"
levels(cc$ncdl)[levels(cc$ncdl)=="76"] <- "71"
levels(cc$ncdl)[levels(cc$ncdl)=="220"] <- "71"
levels(cc$ncdl)[levels(cc$ncdl)=="223"] <- "71"
levels(cc$ncdl)[levels(cc$ncdl)=="67"] <- "71"
levels(cc$ncdl)[levels(cc$ncdl)=="77"] <- "71"
levels(cc$ncdl)[levels(cc$ncdl)=="70"] <- "142"

#fruit and veg
levels(cc$ncdl)[levels(cc$ncdl)=="221"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="50"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="54"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="227"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="243"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="209"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="219"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="243"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="55"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="216"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="246"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="208"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="48"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="207"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="242"] <- "47"

#squash
levels(cc$ncdl)[levels(cc$ncdl)=="249"] <- "222"
levels(cc$ncdl)[levels(cc$ncdl)=="229"] <- "222"

#roots
levels(cc$ncdl)[levels(cc$ncdl)=="247"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="41"] <- "47"
levels(cc$ncdl)[levels(cc$ncdl)=="206"] <- "47"

#vetch, clover, sunflower, mint
levels(cc$ncdl)[levels(cc$ncdl)=="224"] <- "44"
levels(cc$ncdl)[levels(cc$ncdl)=="58"] <- "44"
levels(cc$ncdl)[levels(cc$ncdl)=="6"] <- "44"
levels(cc$ncdl)[levels(cc$ncdl)=="14"] <- "44"

gc()

samples <- fread('samples.csv')
samples$ncdl <- factor(samples$ncdl, levels=levels(cc$ncdl))
levels(samples$ncdl)[levels(samples$ncdl)=="77"] <- "71"
levels(samples$ncdl)[levels(samples$ncdl)=="122"] <- "121"
samples$logc <- log(samples$gcm2)

samples <- samples[!gcm2>20000]
set.seed(1234)

rf <- randomForest(logc ~ nedf + namrad_th + namrad_u + ncdl + slope + matalb + mapalb, data = samples, importance = TRUE, ntree = 512, na.action=na.exclude)

rf
#Call:
# randomForest(logc ~ nedf + namrad_th + namrad_u + ncdl + slope + matalb + mapalb, data = samples, importance = TRUE, ntree = 512, na.action=na.exclude)
#               Type of random forest: regression
#                     Number of trees: 512
#No. of variables tried at each split: 2
#
#          Mean of squared residuals: 0.248831
#                    % Var explained: 20.49

importance(rf)
#            %IncMSE IncNodePurity
#nedf      12.940551      14.06858
#namrad_th  9.327286      11.75251
#namrad_u   7.794047      11.55269
#ncdl      11.206839      12.33659
#slope     12.290106      13.94531
#matalb    15.609760      14.98131
#mapalb    22.160626      19.49296

summary(rf)
#                Length Class   Mode
#call              6    -none-  call
#type              1    -none-  character
#predicted       342    -none-  numeric
#mse             512    -none-  numeric
#rsq             512    -none-  numeric
#oob.times       342    -none-  numeric
#importance       14    -none-  numeric
#importanceSD      7    -none-  numeric
#localImportance   0    -none-  NULL
#proximity         0    -none-  NULL
#ntree             1    -none-  numeric
#mtry              1    -none-  numeric
#forest           11    -none-  list
#coefs             0    -none-  NULL
#y               342    -none-  numeric
#test              0    -none-  NULL
#inbag             0    -none-  NULL
#terms             3    terms   call
#na.action         8    exclude numeric


# we weren't able to fit the entire prediction into memory,
# so we split it into chunks
doprediction <- function() {
  j <- 0
  for(i in seq(from=1, to=302000001, by=1000000)) {
    print(i)
    chunk <- cc[i:(i+1000000)]
    rfpred <- predict(rf, newdata = chunk, predict.all=TRUE)
    outdata <- cbind(cc[i:(i+1000000)]$X, cc[i:(i+1000000)]$Y, rfpred$aggregate, exp(rfpred$aggregate), apply(rfpred$individual, 1, var), (exp(rfpred$aggregate) * apply(rfpred$individual, 1, var)))
    filename <- paste("/workspace/outputs/output", j, ".csv", sep="")
    write.csv(outdata, filename)
    j <- j + 1
    outdata <- NULL
    rfpred <- NULL
    gc()
  }
}

doprediction()

# write out a file with all values
files <- character()
for (i in seq(from=0, to=302, by=1)) {
  filename <- paste("/workspace/outputs/output", i, ".csv", sep="")
  files <- c(files, filename)
}
temp <- lapply(files, fread, sep=",")
pred <- rbindlist(temp)

# fix duplicate column names and remove extra rows at the end
names(pred)[1] <- "V0"
pred <- pred[!is.na(pred$V1),]
write.csv(pred, "/workspace/outputs/rawdata.csv")

# write out the mean raster (exp(log(soc)))
outData <- cbind(pred$V1, pred$V2, pred$V4)
outRaster <- rasterFromXYZ(outData)
writeRaster(outRaster, '/workspace/outputs/msoc.asc')

# write out the variance raster (corrected for log)
outData <- cbind(pred$V1, pred$V2, pred$V6)
outRaster <- rasterFromXYZ(outData)
writeRaster(outRaster, '/workspace/outputs/vsoc.asc')

