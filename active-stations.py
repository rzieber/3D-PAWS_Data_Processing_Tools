import os
from influxdb import InfluxDBClient
import argparse
from pathlib import Path

"""
Step 1: ssh tunnel into the server using the command -- ssh -L 8086:localhost:8086 ubuntu@3d.chordsrt.com
"""

def get_active_stations(host='localhost', port=8086):
    client = InfluxDBClient(
        host=host,
        port=port,
        username='admin',
        password='chords_ec_demo', # fewsnet -- chords_icdp_fewsnet | dr -- 3dpawsdominican | iitm -- chords_bangladesh | 
        database='chords_ts_production'
    )
    
    query = f'''
    SELECT LAST("value") 
    FROM "chords_ts_production"."autogen".tsdata 
    WHERE time > now() - 365d 
    GROUP BY "inst"
    '''
    
    try:
        result = client.query(query)
        
        stations = []
        for key, points in result.items():
            _measurement, tags = key
            inst = tags.get('inst')
            stations.append(inst)

            for point in points:
                print(f"inst: {inst}\t\ttime: {point['time']}\t\tlast reading: {point['last']}")
        
        return stations
    
    except Exception as e:
        print(f"Error querying InfluxDB: {str(e)}")
        return []
    
    finally:
        client.close()

def main(data_path:str, portal:str):
    INFLUX_HOST = os.getenv('INFLUX_HOST', 'localhost')
    INFLUX_PORT = int(os.getenv('INFLUX_PORT', '8086'))
    
    active_stations = get_active_stations(host=INFLUX_HOST, port=INFLUX_PORT)

    try:
        path = Path(data_path)
        filename = f"{portal}_Active-Stations.txt"

        with open(path / filename, 'w', encoding='utf-8', errors='coerce') as file:
            for station in active_stations:
                file.write(f"{station}\n")

    except Exception as e:
        print(e)


def parse_args() -> tuple[str, str]:
    parser = argparse.ArgumentParser(description="Retrieves stations that have been active within the last year and exports them as a text file.")
    
    parser.add_argument("data_path", type=str,   help="Path where data is exported to.")
    parser.add_argument("portal",    type=str,   help="Name of the CHORDS portal.")
    
    args = parser.parse_args()

    return (args.data_path, args.portal)

if __name__ == "__main__":
    main(*parse_args())
