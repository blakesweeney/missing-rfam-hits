process get_dates {
  publishDir 'results', mode: 'copy'

  input:
  path(missing)

  output:
  path('dates.csv')

  """
  fetch_dates.py $missing dates.csv
  """
}

process lookup_sequences {
  input:
  path(missing)

  output:
  path('sequences.fa')

  """
  fetch_sequences.py $missing sequences.fa
  """
}

process fetch_rfam_cm {
  output:
  path('Rfam.cm')

  """
  wget 'https://ftp.ebi.ac.uk/pub/databases/Rfam/14.9/Rfam.cm.gz'
  gzip -d Rfam.cm.gz
  """
}

process scan_sequences {
  publishDir 'results', mode: 'copy'

  input:
  tuple path(sequences), path(rfam)

  output:
  path('hits.txt')

  """
  cmpress $rfam
  cmscan -o output --tblout hits.txt --toponly $rfam $sequences
  """
}

process plot_dates {
  publishDir 'results', mode: 'copy'

  input:
  path(dates)

  output:
  path('publication-dates.png')

  """
  plotDates.R $dates publication-dates.png
  """
}

process build_spreadsheet {
  publishDir 'results', mode: 'copy'

  input:
  path(hits)

  output:
  path('sheet.csv')

  """
  build_spreadsheet.py $hits sheet.csv
  """
}

workflow {
  Channel.fromPath('data/missing.txt') | set { missing }

  fetch_rfam_cm | set { cm }

  missing | get_dates | plot_dates

  missing \
  | lookup_sequences \
  | combine(cm) \
  | scan_sequences \
  | build_spreadsheet
}
