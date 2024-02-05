import os
import time
import datetime
import json
import rapid.process as rp
from minio import Minio
from minio.error import S3Error

#
# Generic module for running a process within jjrom/process-template
#
# On container launch, the execute function is called with input and config dicts
# The input dict contains the process input conform to the application_package json definition
# The config
#
def execute(input, config):
    """
    On container launch, the execute function is called with input and config dicts

            input   -   dict containing the "execute" inputs values conforms to the OGC API Processes
                        description defined within the application_package.json file

            config  -   dict containing variables to be passed to jjromrapid / processApi i.e. the following variables :
                            JOB_AUTH_TOKEN
                            S3_HOST
                            S3_BUCKET
                            S3_KEY
                            S3_SECRET
                            S3_REGION
    """

    #   [ALWAYS DO THAT] 
    #
    #   Initialize resto ProcessAPI 
    #
    processAPI = rp.ProcessAPI()

    #   [ALWAYS DO THAT]
    #
    #   Switch process status from its initial status (i.e. "accepted") to "running"
    #
    processAPI.updateJob(config['JOB_AUTH_TOKEN'], {
        'status':'running'
    })

    #
    #   This is where the process execution start
    #   In this template we simulated a dummy process that last 20s
    #   It is splitted in two to simulate execution progress
    #   You should replace this part with the real process
    #
      
    time.sleep(10)

    #   [OPTIONALLY DO THAT]
    #
    #   Update the progress value accordingly with the process execution
    #
    processAPI.updateJob(config['JOB_AUTH_TOKEN'], {
        'progress': 50
    })
    
    time.sleep(10)

    #
    #   Once the execution is finished, you should fill the process execution outputs
    #   Outputs can be :
    #       - inlined i.e. directly within the result document (e.g. the sum of two number for a summing process)
    #       - physically stored (e.g. the resulting image of an an orthorectification process). In this case, the
    #         result document should contain urls to the data stored in a S3 bucket with HTTP(S) access right.
    #

    #   In our dummy example, the process echoes the inputs replacing trailing "Input" with "Output"

    result = {}
    for key in input['inputs']:
        result[key.replace('Input', 'Output')] = input['inputs'][key]

    #   Here is example of how to store a file to S3 and return its http public url 
    try:
        filePath = "/tmp/process_result.json"
        with open(filePath, "w") as fp:
            json.dump(result, fp)
        url = storeFile(filePath, config)
        print(url)
    except S3Error as exc:
        print("error occurred.", exc)


    #   [ALWAYS DO THAT]
    #
    #   Swith process status from "running" to "successful" or "failed" depending on the result
    #   Note that there is no need to specify the progress value on "successful" since resto will
    #   automatically set it to 100
    #
    processAPI.updateJob(config['JOB_AUTH_TOKEN'], {
        'status': 'successful',
        'result': result
    })

def storeFile(file, config):

    # Initialize Minio client
    client = Minio(
        config['S3_HOST'],
        access_key=config['S3_KEY'],
        secret_key=config['S3_SECRET'],
        # This is to allow http connection on localhost
        secure=False
    )

    # The bucket is created if not exist
    found = client.bucket_exists(config['S3_BUCKET'])
    if not found:   
        client.make_bucket(config['S3_BUCKET'])
    else:
        print('Bucket ' +  config['S3_BUCKET'] + ' already exists')

    objectName = os.path.basename(file)
    client.fput_object(
        config['S3_BUCKET'], objectName, file
    )

    # Return the public GET url valid 1 week
    return client.get_presigned_url(
        "GET",
        config['S3_BUCKET'],
        objectName,
        expires=datetime.timedelta(weeks=1)
    )

