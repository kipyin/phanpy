# A short script on getting the occurance of each flag.
# I've probably spent more time writing these comments than on writing
# the scripts.

# Pandas' `value_counts` is much, much faster.

fullpath = '/Users/Kip/Documents/GitHub/mechanisms/data'
csvpath = paste(fullpath,'/csv/', sep='')
print(csvpath)
setwd(csvpath)

library(plyr)

move.flag.map <- read.csv('move_flag_map.csv')
move.flag.name <- read.csv('move_flags.csv')

move.flag <- merge(x=count(move.flag.map[,-1]),
		  	      y=move.flag.name,
		  	      by.x='x',
		  	      by.y='id')

move.flag <- move.flag[c('identifier', 'freq')]
colnames(move.flag) <- c('move_flag_name', 'freq')


print(move.flag)


outpath = paste(fullpath,'/analysis-R/move_flag_counts.csv', sep='')

if (file.exists(outpath)) {file.remove(outpath)}

write.csv(move.flag,
		 file= outpath,
		 quote=FALSE)
