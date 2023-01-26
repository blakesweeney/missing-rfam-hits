#!/usr/bin/env Rscript

library(tidyverse)
library(lubridate, warn.conflicts = FALSE)

args = commandArgs(trailingOnly=TRUE)

data <- read_csv(args[1])
output_file <- args[2]

data$date <- ymd(data$date)

plot <- ggplot(data, aes(x=date)) + geom_histogram(binwidth=30)

ggsave(output_file, plot, device="png")
