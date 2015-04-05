# srtfix
simple python script for modifying the sync time of a subtitles file

Usage: <code>strfix.py filename offset </code> <br><br>
Arguments: 
<ul>
	<li><i>filename</i> is a path to the .srt or .txt you want to modify </li>
	<li><i>offset</i> is a valid offset on the form: 
		<ul>	
			<li>+xxhxxmxxsxxxms (h=hours, m=minutes, s=seconds, ms=milliseconds) if you want to shift the time ahead </li>
			<li>-xxhxxmxxsxxxms (h=hours, m=minutes, s=seconds, ms=milliseconds) if you want to shift the time back </li>
		</ul>
	</li>	

</ul>
	 
