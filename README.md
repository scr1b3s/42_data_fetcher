# 42 Data Fetcher

A simple Python client that requests the École 42 API to collect relevant data about the training background and historical data for it's cadets.

# TODO:
- Turn the Extraction Functions into a Class: DF_Data_Extractor.
- Think about how the extraction process is being made, in __main__ instead of functions that're called inside a __main__ if needed.
  - I think it's better to use the extracting action process in functions, since it's easier to iterate over when using Data Orchestrators... but we'll see.
- Where should the data go?