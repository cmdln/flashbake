if checkProcess("iTunes") then
	tell application "iTunes"
		if player state is playing then
			set trck to current track
			set title_text to (get name of trck)
			set artist_text to (get artist of trck)
			set album_text to (get album of trck)
			set playpos to (get player position)
			set displayTime to (my calc_total_time(playpos))
			set title_time to (get time of trck)
			set rate to (get rating of trck) / 20
		
			set rate_text to ""
		
			repeat rate times
				set rate_text to rate_text & " * "
			end repeat
		
			set body_text to title_text & "
" & artist_text & " - " & album_text & "
" & displayTime & "/" & title_time & " - " & rate_text
		
		else
			set body_text to "Nothing playing in iTunes"
		end if
	end tell
else
	set body_text to "iTunes is not open"
end if

----------------------------------------------------------------
to calc_total_time(totalSeconds)
	set theHour to totalSeconds div 3600
	if theHour is not 0 then
		copy (theHour as string) & ":" to theHour
	else
		set theHour to ""
	end if
	set theMinutes to (totalSeconds mod 3600) div 60
	if theMinutes is not 0 then
		--if theMinutes is less than 10 then set theMinutes to "0" & (theMinutes as string)
		copy (theMinutes as string) & ":" to theMinutes
	else
		set theMinutes to "0:"
	end if
	set theSeconds to totalSeconds mod 60
	if theSeconds is less than 10 then set theSeconds to "0" & (theSeconds as string)
	return theHour & theMinutes & theSeconds as string
end calc_total_time


----------------------------------------------------------------

on checkProcess(processName)
	tell application "System Events"
		set isRunning to ((application processes whose (name is equal to processName)) count)
	end tell
	if isRunning is greater than 0 then
		return true
	else
		return false
	end if
end checkProcess