import salabim as sim 
import random



#PRANCHAS
class Pressing(sim.Component):
	def process(self):
		while True:
			yield self.wait((work_control,'working'))
			yield self.hold(pressing_time.sample())
			Deck()

class Deck(sim.Component):
	def process(self):
		self.enter(armazem)
		yield self.passivate()

		self.enter(cutwaitingline)
		yield self.request(cuttings)
		yield self.wait((work_control,'working'))
		yield self.hold(cutting_time.sample())
		self.release(cuttings)
		self.leave(cutwaitingline)

		self.enter(finwaitingline)
		yield self.request(finishing)
		yield self.wait((work_control,'working'))
		yield self.hold(finishing_time.sample())
		self.release(finishing)
		self.leave(finwaitingline)
  
		self.enter(paintwaitingline)
		yield self.request(painting)
		yield self.wait((work_control,'working'))
		yield self.hold(painting_time.sample())
		self.release(painting)
		self.leave(paintwaitingline)
		
		self.enter(armazem2)
		yield self.passivate()
		
		deck_unity.set_capacity(deck_unity.capacity()+24)

		


#RODAS
class Foundry(sim.Component):
	def process(self):
		while True:
			yield self.wait((work_control,'working'))
			yield self.hold(foundry_time.sample())
			Wheel()
			
class Wheel(sim.Component):
	def process(self):
		global skates
		global wheel_pack
		self.enter(armazem3)
		yield self.passivate()

		self.enter(machiningwaitingline)
		yield self.request(machining)
		yield self.wait((work_control,'working'))
		yield self.hold(machining_time.sample())
		self.release(machining)
		self.leave(machiningwaitingline)

		self.enter(printingwaitingline)
		yield self.request(printing)
		yield self.wait((work_control,'working'))
		yield self.hold(printing_time.sample())
		self.release(printing)
		self.leave(printingwaitingline)

		self.enter(armazem4)
		
		yield self.passivate()
		wheel_unity.set_capacity(wheel_unity.capacity()+192)
	
class packingDeck(sim.Component):
	def process(self):
		while True:			
			yield self.request(deck_pack)
			yield self.request(packing_d,(deck_unity,96))
			yield self.wait((work_control,'working'))
			yield self.hold(pack_d_time.sample())
			yield self.release(packing_d)
			

class packingWheel(sim.Component):
	def process(self):
		while True:	
			yield self.request(wheel_pack)
			yield self.request(packing_w,(wheel_unity,192))
			yield self.wait((work_control,'working'))
			yield self.hold(pack_w_time.sample())
			yield self.release(packing_w)
			

class Assembly_Line(sim.Component):
	def process(self):
		while True:
			yield self.request(skate_unity)
			yield self.request(assembly_line,(deck_unity,24))
			yield self.request(assembly_line,(wheel_unity,96))
			print(wheel_unity.capacity(),'')
			print(deck_unity.capacity())
			yield self.wait((work_control,'working'))
			yield self.hold(assembly_time.sample())
			yield self.release(assembly_line)
			

			
class Gestao(sim.Component):
	def process(self):
		while True:
			yield self.passivate()
			if(deck_unity.available_quantity() > 432):
				if(env.now()//1440 % 3 == 0):
					deck_pack.set_capacity(deck_pack.capacity()+12*1)
				else:
					deck_pack.set_capacity(deck_pack.capacity()+12*2)

			if(wheel_unity.available_quantity() > 1536):
				if(env.now()//1440 % 2 == 0):
					wheel_pack.set_capacity(wheel_pack.capacity()+48*2)
				else:
					wheel_pack.set_capacity(wheel_pack.capacity()+48*3)
			skate_unity.set_capacity(skate_unity.capacity() + 1*24*10)

#Gestao da hora de trabalho
class WorkTimeControl(sim.Component):
	def process(self):
		while True:
			work_control.set('working')
			yield self.hold(480)
			work_control.set('not_working')
			yield self.hold(960)
			while len(armazem) > 0:
				self.Deck = armazem.pop()
				self.Deck.activate()
			while len(armazem2) > 0:
				self.Deck = armazem2.pop()
				self.Deck.activate()
			while len(armazem3) > 0:
				self.Wheel = armazem3.pop()
				self.Wheel.activate()
			while len(armazem4) > 0:
				self.Wheel = armazem4.pop()
				self.Wheel.activate()
			if(env.now()//1440) > 1:
				gestao.activate()

env = sim.Environment(random_seed=200,time_unit ='minutes',trace=False)



work_control = sim.State('work_control',value = 'working')


#initiation dos processos
deck_pack = sim.Resource('deck_pack',capacity = 0)
wheel_pack = sim.Resource('wheel_pack',capacity = 0)
skate_unity = sim.Resource('skate_unity',capacity = 0)
wheel_unity = sim.Resource('wheel_unity',capacity = 0)
deck_unity = sim.Resource('deck_unity',capacity = 0)
cuttings = sim.Resource('cuttings',capacity = 3)
finishing = sim.Resource('finishing',capacity = 1)
painting = sim.Resource('painting', capacity = 1)
machining = sim.Resource('machining',capacity = 2)
printing = sim.Resource('printing', capacity = 1)
packing_w = sim.Resource('packing_w',capacity = 1)
packing_d = sim.Resource('packing_d',capacity = 2)
assembly_line = sim.Resource('assembly_line',capacity = 2)

work_time = WorkTimeControl()
pressings = [Pressing() for _ in range(4)]
foundry = Foundry()
gestao = Gestao()
packingDeck = [packingDeck() for _ in range(2)]
packingWheel = packingWheel()
assemblyLine = Assembly_Line()

#Filas de espera
cutwaitingline = sim.Queue("cutwaitingline")
finwaitingline = sim.Queue("finwaitingline")
paintwaitingline = sim.Queue("paintwaitingline")
deckwaitingline = sim.Queue("deckwaitingline")
assemblywaitingline = sim.Queue("assemblywaitingline")
machiningwaitingline = sim.Queue("machiningwaitingline")
printingwaitingline = sim.Queue("printingwaitingline")
wheelwaitingline = sim.Queue("wheelwaitingline")


#armazens
armazem = sim.Queue("armazem")
armazem2 = sim.Queue("armazem2")
armazem3 = sim.Queue("armazem3")
armazem4 = sim.Queue("armazem4")

#distributions
pressing_time = sim.Triangular(95,105,100)
cutting_time = sim.Triangular(50,70,60)
finishing_time = sim.Triangular(5,25,15)
painting_time = sim.Triangular(10,30,20)
foundry_time = sim.Triangular(50,60,55)
machining_time = sim.Triangular(55,65,60)
printing_time = sim.Triangular(15,25,20) 
pack_d_time = sim.Triangular(0,20,10)
pack_w_time = sim.Triangular(25,35,30)
assembly_time = sim.Triangular(20,40,30)
#configs

env.run(till=24*60*24)

print(wheel_pack.capacity(),'conjunto de rodas')
print(skate_unity.capacity(),'skates')
print(deck_pack.capacity(),'caixas de pranchas')
