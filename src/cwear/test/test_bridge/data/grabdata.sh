#!/bin/bash -x
#
# Grab data for testing from humanapi
#

function grab_batch() {  # (endpoint)
    endpoint=$1
    curl -X GET -H 'Accept: application/json' -u 0f3692b3d7fa24279e5ea2eebe31b2e7866392bd: "https://api.humanapi.co/v1/apps/683ef654510ba8d03579f5717a90657cb21d7ebd/users/${endpoint}" > "${endpoint}.json"
}

grab_batch "activities"
grab_batch "heart_rates"
grab_batch "bmis"
grab_batch "body_fats"
grab_batch "heights"
grab_batch "weights"
grab_batch "blood_glucoses"
grab_batch "blood_oxygens"
grab_batch "sleeps"
grab_batch "blood_pressures"
grab_batch "genetic_traits"
grab_batch "locations"
