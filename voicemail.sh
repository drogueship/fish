#!/bin/bash

exec 2>> /var/tmp/answering-machine.out

# Answering machine script for vgetty
# Also see http://alpha.greenie.net/vgetty/readme.voice_shell.html

#INDIR="/home/pi/voicemail"
INDIR="/var/www/html/voicemail"
OUTDIR="/var/spool/voice/messages"

OUT_MSG="${OUTDIR}/heyhowyoudoin.rmd"

# This is the format for filenames:
#NAME="${INDIR}/$(date +%F.%T).${CALLER_ID}.${CALLER_NAME}.${SUBJECT}"
NAME="${INDIR}/$(date +%F.%H-%M-%S)"
FNAME=$(echo "$NAME" | tr ' ' '+')


export PATH="/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin"
PROGNAME="$0"

# the function to receive an answer from the voice library
function receive {
     read -r INPUT <&$VOICE_INPUT;
     echo "$INPUT";
}

# the function to send a command to the voice library
function send {
     echo $1 >&$VOICE_OUTPUT;
     kill -PIPE $VOICE_PID
}

function expect {
    if [ "$1" != "$(receive)" ]; then
        echo "${PROGNAME}: $2" >> /var/tmp/answering-machine.out
        exit 0
    fi
}

function exch {
    send "$1"
    expect "$2" "$3"
}

function log {
    echo "$*" >> /var/tmp/answering-machine.out
}


echo "swim" | nc 127.0.0.1 5000 &

ANSWER=`receive`

if [ "$ANSWER" != "HELLO SHELL" ]; then
    echo "$0: voice library not answering" >&2
    exit 1
fi

send "HELLO VOICE PROGRAM"

ANSWER=`receive`

    if [ "$ANSWER" != "READY" ]; then
        echo "$0: initialization failed" >&2
        exit 1
    fi

send "DEVICE DIALUP_LINE"

ANSWER=`receive`

if [ "$ANSWER" != "READY" ]; then
    echo "$0: could not set output device" >&2
    exit 1
fi

if [ -f $OUT_MSG ]; then
    send "PLAY $OUT_MSG"

    ANSWER=`receive`

    if [ "$ANSWER" != "PLAYING" ]; then
        echo "$0: could not start playing" >&2
        exit 1
    fi


    ANSWER=`receive`

    if [ "$ANSWER" != "READY" ]; then
        echo "$0: something went wrong on playing" >&2
        exit 1
    fi

fi

    send "BEEP"
    ANSWER=`receive`

    if [ "$ANSWER" != "BEEPING" ]; then
        echo "$0: could not send a beep" >&2
        exit 1
    fi

    ANSWER=`receive`

    if [ "$ANSWER" != "READY" ]; then
        echo "$0: could not send a beep" >&2
        exit 1
    fi

#send "ENABLE EVENTS"
#ANSWER=`receive`
#if [ "$ANSWER" != "READY" ]; then
#    echo "$0: that's weird, it said $ANSWER" >&2
#fi

    send "RECORD ${FNAME}.rmd"

   log "about to receive events"


while true; do
    ANSWER=`receive`

log "in recording condition"
case $ANSWER in
        RECORDING)
            ANSWER=`receive`
            case $ANSWER in
				READY)
					send "STOP"
					receive
					send "GOODBYE"
					receive
					log "READY"
					break
					;;
				RECEIVED_DTMF) 
					break
					;;
				BUSY_TONE) 
					send "STOP"
					receive
					send "GOODBYE"
					receive 
					log "BUSY" 
					break
					;;
                FAX_CALLING_TONE) 
					send "STOP"
					receive
					send "GOODBYE"
					receive
					log "FAX_CALLING_TONE"
					break
					;;
                *) 
					send "STOP"
					receive 
					send "GOODBYE" 
					receive
					log "$ANSWER" 
					break
					;;
        	esac
			;;
	esac

done

#send "GOODBYE"
#ANSWER=`receive`

#    if [ "$ANSWER" != "GOODBYE SHELL" ]; then
#        echo "$0: could not say goodbye to the voice library" >&2
#        exit 1
#    fi


# exit 0

# Format it
if rmdtopvf "${FNAME}.rmd" | pvftowav > "${NAME}.wav"; then
    rm "${FNAME}.rmd"
    chown www-data "${NAME}.wav"
fi

echo "lift_head" | nc 127.0.0.1 5000 &
sleep 1
echo "start_listen" | nc 127.0.0.1 5000 &
sleep 2

#FISH_LISTENER=$!

play ${NAME}.wav

echo "lower_head" | nc 127.0.0.1 5000 &
sleep 1
echo "stop_listen" | nc 127.0.0.1 5000 &
sleep 1

# Change the owner of the voicemail file so a CGI can manipulate it
# chown apache "${NAME}.wav" || exit 1

exit 0
