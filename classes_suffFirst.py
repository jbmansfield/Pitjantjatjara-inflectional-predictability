	
class Cell:
	def __init__(self, mps, vc, form, pros, aug, suff):
		self.mps = mps
		self.vc = vc
		self.form = form
		self.cues = {
			'cueless': 'cueless',
			'suff': suff,
			'augSuff': '-'.join([aug, suff]),
			'prosAugSuff': '-'.join([pros, aug, suff])
		}
		self.pros = pros
		self.aug = aug
		self.suff = suff
		self.avgEnt = {
			'cueless': 0,
			'suff': 0,
			'augSuff': 0,
			'prosAugSuff': 0
		}

	def __str__(self):
		features = '_'.join([self.vc, self.mps])
		return ':'.join([features, self.form])
