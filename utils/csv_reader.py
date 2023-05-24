import csv

class CsvReader:
    # La funcion read_csv_file retorna un objeto diccionario
    def read_csv_file(self):
        csvReader = csv.DictReader(open('test_data\datos.csv'))
        return csvReader

    # La funcion read_csv_file retorna un objeto List
    def read_csv_List(self):
        with open('test_data\datos.csv') as csvfile:
            csvReader = csv.reader(csvfile, delimiter=',')
            return csvReader
