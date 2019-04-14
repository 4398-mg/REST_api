import os, sys, shutil
import pretty_midi

# Name directory to crawl. Cannot contain subdirectories.
songs_directory = "" #@Ishan: If you find it easier, you can set the variable here instead.
if "--location" in sys.argv: # command line option to choose folder to filter
	songs_directory = sys.argv[sys.argv.index("--location") + 1]
else:
	print ("Set --location option to choose folder to clean.")
	exit() #@Ishan if you do that, you need to remove this exit()
if songs_directory[-1] != "/":
	songs_directory += "/"

# Name directory to place bad files in.
bad_files_directory = "" #@Ishan: If you find it easier, you can set the variable here instead.
if "--dump" in sys.argv: # command line option to choose place to leave bad MIDIs
	bad_files_directory = sys.argv[sys.argv.index("--dump") + 1]
else:
	print ("Set --dump option to choose where to move files")
	exit() #@Ishan if you do that, you need to remove this exit()
if bad_files_directory[-1] != "/":
	bad_files_directory += "/"

# Ensure dump directory exists
bad_files_directory_path_components = bad_files_directory.split("/")
validated_path = ""
for dir in bad_files_directory_path_components:
	try:
		os.listdir(validated_path + dir)
	except OSError as e:
		os.mkdir(validated_path + dir)
	finally:
		validated_path += dir + "/"

# midi_data = pretty_midi.PrettyMIDI("data/classical/2_ase.mid")
# midi_data = pretty_midi.PrettyMIDI("data/classical/Carulli_Concerto_Flauto_Chitarra_Orchestra_Allegro.mid")

# Open file for log of files removed.
log_file_name = "removed_files.csv"

# Try every song for validity
for song in os.listdir(songs_directory):
	index = 0
	try:
		midi_data = pretty_midi.PrettyMIDI(songs_directory + song)
	except RuntimeWarning as e:
		bad_files_log = open(log_file_name, "a")
		print ("Found bad MIDI " + song)
		bad_files_log.write(song + "\n")
		# Close immediatedly so that interrupts don't wipe out the log.
		bad_files_log.close()
		shutil.move(songs_directory + song, bad_files_directory + song)
	# else:
		# print ("Succeeded in importing " + song)
	except Exception:
		bad_files_log = open(log_file_name, "a")
		print ("Likely bad MIDI " + song)
		bad_files_log.write(song + "\n")
		# Close immediatedly so that interrupts don't wipe out the log.
		bad_files_log.close()
		shutil.move(songs_directory + song, bad_files_directory + song)
	finally:
		index += 1
		if index % 50 == 0:
			print ("chug ... chug")
	
#bad_files_log.close()