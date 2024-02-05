#!/bin/bash
. /etc/profile
ldconfig /
process=$1
shift;
case "$process" in
    deploy)
        exec deploy /process/application_package.json "$@"
        ;;
    replace)
        exec replace /process/application_package.json "$@"
        ;;
    undeploy)
        exec undeploy /process/application_package.json "$@"
        ;;
    execute)
        exec execute "$@"
        ;;
    *)
        echo $"Usage: $0 {deploy|replace|undeploy|execute}"
        exit 1
esac
