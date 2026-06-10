classdef ICA < ECA
	%------------------------------------------------------------------------
	%    A 1-dimensional ising cellular automata(ICA), incorporating both 
	%    stochastic and deterministic evolution
	% 
	%    Create an ICA:
	%          myICA = ICA(RULE,STATE,TEMPERATURE,STOCHASTIC_FRACTION)
	%    The RULE needs to be an integer, 0-255, and the STATE must be a row
	%    vector of 0s and 1s. The TEMPERATURE must be a nonnegative real 
	%	   number. The STOCHASTIC_FRACTION is a real number in [0,1].
	%
	%    Questions or comments? DRSowinski@gmail.com
	%
	%    COPYRIGHT 2016 Damian Radoslaw Sowinski
	%------------------------------------------------------------------------
  
	
  properties %------------------------------------------- PUBLIC PROPERTIES
    energy          %The Ising energy of the state
    temperature     %The temperature needed to evolve stochastically
    stochfrac       %The percentage of cells that evolve stochastically
  end %-------------------------------------------------------------*
  
  properties (Access = protected) %-------------------- PRIVATE PROPERTIES
    invT
  end %-------------------------------------------------------------*

  
	
  methods %------------------------------------------------ PUBLIC METHODS
    %------------------------------- object constructor and setters
    function obj = ICA(rule,state,temperature,stochfrac)
      narginchk(4,4)
      obj@ECA(rule,state);
      obj.temperature = temperature;
      obj.stochfrac = stochfrac;
      obj.energy = mean(obj.getStateEnergy());
    end 
    function set.temperature(obj,newTemperature)
      validateattributes(newTemperature,{'numeric'},{'scalar',...
        'nonnegative'})
      obj.temperature = newTemperature;
      obj.invT = 1/(eps+newTemperature);
    end
    function set.stochfrac(obj,newStochFrac)
      validateattributes(newStochFrac,{'numeric'},{'scalar',...
        '>=' 0,'<=' 1})
      obj.stochfrac = newStochFrac;
    end
    %---------------------------------------------------- functions
    function evolve(obj)
      stochCellIdx = find(rand([1,obj.N])<obj.stochfrac);
      stochCellVal = obj.state(stochCellIdx);
      stateEnergy = obj.getStateEnergy();
      obj.energy = sum(stateEnergy)/obj.N;
      flippedIdx = obj.stochEvolve(stateEnergy(stochCellIdx));
      stochCellVal(flippedIdx)=1-stochCellVal(flippedIdx);
      state = obj.caRule;
      state(stochCellIdx)=stochCellVal;
      obj.state = state;
    end
  end %-----------------------------------------------------------*

  methods (Access = protected)  %------------------------- PRIVATE METHODS
    function stateEnergy = getStateEnergy(obj)
      isingArray = 2*obj.state-1;
      stateEnergy = .5*(circshift(isingArray,[0,1]) +...
        circshift(isingArray,[0,-1]));
      stateEnergy = -isingArray.*stateEnergy;
    end
    function flippedStates = stochEvolve(obj,stateEnergy)
      flippedStates = find(rand([1,length(stateEnergy)]) <...
         1./(1+exp(-2*obj.invT*stateEnergy)));
    end
  end %-----------------------------------------------------------*
end
