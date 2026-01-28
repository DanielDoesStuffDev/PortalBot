# there would usually be a bitreader for a demo parser
# but we don't really need any information other than the header
# and the packet ticks and sizes which are all aligned
# so i'll use a bytereader instead

import struct
from discord import Embed
import responses

class Reader:
	def __init__(self, data) -> None:
		self.data = data
		self.index = 0


	# most of these functions take in an "amount"
	# THIS IS MEASURED IN BYTES NOT BITS!!!!


	def read_bytes(self, amount: int) -> bytes:
		res = self.data[self.index : self.index + amount]
		self.index += amount
		return res


	def skip(self, amount: int) -> None:
		self.index += amount


	def read_string_nulled(self) -> str:
		# self.data.index(0x00, self.index) finds the closest 0x00 (null terminator byte)
		return self.read_bytes(self.data.index(0x00, self.index) - self.index).decode("ascii")


	def read_string(self, amount: int) -> str:
		return self.read_bytes(amount).decode("ascii")


	# in demos the vast majority of ints are signed
	def read_int(self, amount: int, signed=True) -> int:
		return int.from_bytes(self.read_bytes(amount), byteorder="little", signed=signed)


	def read_float(self, amount: int) -> float:
		return round(struct.unpack('<f', self.read_bytes(amount))[0], 3)


class Demo:
	def __init__(self) -> None:
		self.file_stamp = ""
		self.demo_protocol = 0
		self.network_protocol = 0
		self.server_name = ""
		self.client_name = ""
		self.map_name = ""
		self.game_directory = ""
		self.playback_time = 0.0
		self.playback_ticks = 0
		self.playback_frames = 0
		self.sign_on_length = 0
		self.ticks = []


class Parser:
	def __init__(self, data) -> None:
		self.reader = Reader(data)
		self.demo = Demo()


	def parse_demo(self):
		try:
			# check file stamp
			self.demo.file_stamp = self.reader.read_string(8)
			if self.demo.file_stamp != "HL2DEMO\0":
				print(f"{self.demo.file_stamp}")
				self.demo = Demo()
				return

			self.demo.demo_protocol = self.reader.read_int(4)
			self.demo.network_protocol = self.reader.read_int(4)
			self.demo.server_name = self.reader.read_string(260)
			self.demo.client_name = self.reader.read_string(260)
			self.demo.map_name = self.reader.read_string(260)
			self.demo.game_directory = self.reader.read_string(260)
			self.demo.playback_time = self.reader.read_float(4)
			self.demo.playback_ticks = self.reader.read_int(4)
			self.demo.playback_frames = self.reader.read_int(4)
			self.demo.sign_on_length = self.reader.read_int(4)

			
	# 		# Save Tick
	# 		print(responses.print_colour("B", 
	# 								f"""
	# Reading Demo...
	# Playback Ticks: {tick}"""))
	# 		demos_ticks = []
	# 		with open("./demo_info/archive_demo_info.txt", "r") as file:
	# 			for line in file.readlines():
	# 				demos_ticks.append(int(line))
	# 			file.close()
	# 		demos_ticks.append(tick)

	# 		with open("./demo_info/archive_demo_info.txt", "w") as file:
	# 			for value in demos_ticks:
	# 				file.write(f"{value}\n")
	# 			file.close()

			while self.reader.index < len(self.reader.data):
				packet_type = self.reader.read_int(1)
				tick = self.reader.read_int(4)
				if tick not in self.demo.ticks and tick >= 0:
					self.demo.ticks.append(tick)
					with open("./demo_info/archive_demo_info.txt", "a") as file:
						file.write(f"{tick}\n")
						

				match packet_type:
					case 7:
						# STOP packet
						break
					case 1 | 2:
						# SINGON packet
						
						# skip cmd_info, in/out sequence
						self.reader.skip(76 + 4 + 4)
						self.reader.skip(self.reader.read_int(4))
					case 3:
						# SYNCTICK packet
						# contains no data
						pass
					case 4:
						# CONSOLE CMD packet
						# contains a string, will be useful for time adjustment later
						self.reader.skip(self.reader.read_int(4))
					case 5:
						# USER CMD packet
						# will also be useful for time adjustment later

						# skip cmd
						self.reader.skip(4)
						self.reader.skip(self.reader.read_int(4))
					case 6:
						# DATATABLES packet
						# will most likely not be useful here
						self.reader.skip(self.reader.read_int(4))
					case 8:
						# STRINGTABLES packet
						# will most likely not be useful here
						self.reader.skip(self.reader.read_int(4))
			file.close()
		except Exception as e:
			print(responses.print_colour("R", f"Error parsing demo: {e}"))


	def generate_embed(self, filename: str) -> Embed:
		total_ticks = 0
		with open("./demo_info/archive_demo_info.txt", "r") as file:
			for line in file.readlines():
				total_ticks += 1
			print(responses.print_colour("B", f"{total_ticks}"))
		ticks_len = total_ticks
		seconds = ticks_len * 0.015
		minutes = round(seconds // 60)
		if minutes == 0:
			time_str = str(seconds)
			if len(time_str.split(".")[1]) == 2:
				time_str += "0"
		else:
			if seconds - minutes * 60 < 10:
				time_str = str(minutes) + ":0" + str(seconds - minutes * 60)
			else:
				time_str = str(minutes) + ":" + str(seconds - minutes * 60)
			if len(time_str.split(".")[1]) == 2:
				time_str += "0"

		res_embed = Embed(title=f"Successfully parsed {filename}!", color=0x00ff00)
		# dont display file stamp cause its just HL2DEMO for every demo
		res_embed.add_field(name="Demo Protocol", value=self.demo.demo_protocol)
		res_embed.add_field(name="Network Protocol", value=self.demo.network_protocol)
		res_embed.add_field(name="Server Name", value=self.demo.server_name)
		res_embed.add_field(name="Client Name", value=self.demo.client_name)
		res_embed.add_field(name="Map Name", value=self.demo.map_name)
		res_embed.add_field(name="Game Directory", value=self.demo.game_directory)
		res_embed.add_field(name="Playback Time", value=self.demo.playback_time)
		res_embed.add_field(name="Playback Ticks", value=self.demo.playback_ticks)
		res_embed.add_field(name="Playback Frames", value=self.demo.playback_frames)
		res_embed.add_field(name="SignOn Length", value=self.demo.sign_on_length)
		res_embed.add_field(name="Measured Time", value=time_str)
		res_embed.add_field(name="Measured Ticks", value=ticks_len)

		return res_embed