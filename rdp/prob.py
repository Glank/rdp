import math

class ProbabilitySet:
    def __contains__(self, obj):
        """Returns true if 'obj' might be in this set or
        false if it definately isnt."""
        return self.getProbability(obj)>0
    def getProbability(self, obj):
        """Returns the approximate probability (ceteris paribus)
        of 'obj' being in this set."""
        raise NotImplementedError()
    def getInformationPacket(self, obj, inst):
        """See Entropy(Information Theory)
        http://en.wikipedia.org/wiki/Entropy_%28information_theory%29"""
        return InformationPacket(
            inst, -math.log(self.getProbability(obj))
        )

class JoinedProbabilitySet(ProbabilitySet):
    def __init__(self, prob_sets, weights=None):
        assert(len(prob_sets)>=2)
        if weights is None:
            weights = [1 for p in prob_sets]
        self.prob_sets = prob_sets
        self.weights = weights
    def __contains__(self, obj):
        return all((obj in ps) for ps in self.prob_sets)
    def getProbability(self, obj):
        probs = [ps.getProbability(obj) for ps in self.prob_sets]
        infos = [-w*math.log(p) for w,p in zip(self.weights,probs)]
        return math.exp(-sum(infos))

class InformationPacket:
    """Using information theory because I'm a pedant."""
    def __init__(self, obj, info_content):
        self.obj = obj
        self.info_content = info_content
    def __repr__(self):
        return repr(self.obj)+": %f"%self.info_content
