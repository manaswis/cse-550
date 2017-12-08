import os
from os.path import expanduser
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine

import urllib
import math
import pandas as pd

def connect_to_db():

    dbhost = 'localhost'
    dbport = str(5432)
    dbname = 'sidewalkturk'
    dbuser = 'sidewalk'
    dbpass = 'sidewalk'

    # Format of the connection string: dialect+driver://username:password@host:port/database
    connection_str = ('postgresql://' + dbuser + ':' + dbpass +
                      '@' + dbhost + ':' + dbport + '/' + dbname)
    print connection_str
    engine = create_engine(connection_str)
    conn = psycopg2.connect("dbname=" + dbname +
                            " user=" + dbuser +
                            " host=" + dbhost +
                            " port=" + dbport +
                            " password=" + dbpass + "")

    return conn, engine

if __name__ == '__main__':
    
    # Connect to PostgreSQL database
    conn, engine = connect_to_db()

    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # First pass: 35 labels
    easy = [1433, 1457, 1460,1469,1478,1429,1437,1471,1475] #26 labels
    medium = [1434,1449,1472,1473,1479,1513,1535,1557,1564] #20 labels
    hard = [1438,1440,1458,1465,1480,1495,1520,1575,1578,1583,
            1605,1606,1616,1624,1632,1634,1638] #26 labels
    
    # Get all the metadata for the labels given the cluster ids
    # Metadata: (label_id, cluster_id, heading, pitch, zoom, panoid, label_type,) from gt_label
    labels = []
    
    for cluster_list_i in [easy, medium, hard]:
        list_i = ','.join(str(e) for e in cluster_list_i)
        print "Cluster Ids: " + list_i
        cursor.execute(
            """select label_id, cluster_id, pano_id, heading, pitch, zoom, l.description as marked_label, l.description as correct_label
                from (select gt_labels.gt_label_id as label_id, clustering_session_cluster_id as cluster_id, gsv_panorama_id as pano_id, heading, pitch, zoom, label_type_id as l_id 
                        from (select gt_label_id, clustering_session_cluster_id
                                from gt_existing_label as gtl, 
                                    (select clustering_session_cluster_id, label_id 
                                    from clustering_session_label 
                                    where clustering_session_cluster_id in (%s) 
                                    ) as hard_labels
                                where gtl.label_id = hard_labels.label_id) 
                             as gt_labels, gt_label as gt
                        where gt_labels.gt_label_id = gt.gt_label_id)
                     as metadata, label_type as l
                where l.label_type_id = metadata.l_id;""" % list_i)
        metadata_rows = cursor.fetchall()

        for row in metadata_rows:
            labels.append(row)

    labels_df = pd.DataFrame(labels, columns=['label_id', 'cluster_id', 'pano_id', 'heading', 'pitch', 'zoom',
                                             'marked_label', 'correct_label'])
    labels_df['hard_level'] = 'undefined'
    labels_df.ix[labels_df.index<=9, 'hard_level'] = 'easy'
    labels_df.ix[labels_df.index >= 20, 'hard_level'] = 'hard'
    labels_df.ix[labels_df['hard_level'] == 'undefined', 'hard_level'] = 'medium'

    # Download image, update pd, and save image
    labels_df['img_filename'] = ''
    for index, row in labels_df.iterrows():

        pano_id = row['pano_id']
        heading = str(row['heading'])
        pitch = str(row['pitch'])
        zoom = row['zoom']
        fov = str(180 / math.pow(2,zoom))
        
        hard_level = str(row['hard_level'])
        cluster_id = str(row['cluster_id'])
        label_id = str(row['label_id'])
        img_filename = hard_level + '_' + cluster_id + '_' + label_id + '_' + pano_id + '.jpeg'
        labels_df.ix[index,'img_filename'] = img_filename

        gsv_url = ("https://maps.googleapis.com/maps/api/streetview?size=720x480&pano=%s&heading=%spitch=%s&fov=%s&key=AIzaSyDzYR4m-3upEQ-bIQam35ixN1BgxnPsY7k" 
                    % (pano_id, heading, pitch, fov))
        response = urllib.urlretrieve(gsv_url, 'static/test_images/' + img_filename)

    print(labels_df)
    labels_df.to_csv('labels_1.csv')

