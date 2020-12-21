classdef ECA < handle
    %------------------------------------------------------------------------
    %    A 1-dimensional elementary cellular automata(ECA) class as described
    %    in http://mathworld.wolfram.com/ElementaryCellularAutomaton.html
    %
    %    Create an ECA:
    %          myECA = ECA(RULE,STATE)
    %    The RULE needs to be an integer, 0-255, and the STATE must be a row
    %    vector of 0s and 1s. Change either of these properties by via:
    %          myECA.rule = newRule
    %          myECA.state = newState
    %    The EVOLVE method updates the ECA one time step, whereas the PLAY
    %    method evolves the ECA and displays it until the user presses a key.
    %
    %    Questions or comments? DRSowinski@gmail.com
    %
    %    COPYRIGHT 2016 Damian Radoslaw Sowinski
    %------------------------------------------------------------------------
    
		
    properties %------------------------------------------- PUBLIC PROPERTIES
        rule          % a number between 0-255
        state         % a row array of 0s and 1s
    end %-------------------------------------------------------------*
    
    properties (Access = protected) %------------------- PROTECTED PROPERTIES
        ruleArray     % used to implement the rule mapping
        memoryLength  % how much of the history is remembered
        pastStates    % the history of the CA
        dispHeight    % duh
        dispWidth     % duh
        N             % size of the CA
    end %-------------------------------------------------------------*
    
		
		
    methods %------------------------------------------------- PUBLIC METHODS
        %------------------------------- object constructor and setters
        function obj = ECA(rule,state)
            narginchk(0,2) %check for correct number of inputs
            if nargin == 0
		disp('Initializing with random rule and state')
		obj.rule = randi([0,255],1)
		obj.state = randi([0,1],[1,32])
	    end
	    obj.state = state;
            obj.rule = rule;
            
            obj.N = length(state);
            obj.memoryLength = max(min(3*obj.N,5000),300);
            obj.dispWidth = min(obj.N/2560,1);
            obj.dispHeight = min(obj.memoryLength/1440,1);
            obj.pastStates = -ones([obj.memoryLength,obj.N]);
        end
        function set.rule(obj,newRule)
            validateattributes(newRule,{'numeric'},{'scalar','integer',...
                'nonnegative','<=' 255})
            obj.rule = newRule;
            obj.updateRuleArray();
        end
        function set.state(obj,newState)
            validateattributes(newState,{'numeric'},{'row','binary'})
            obj.state = newState;
            obj.updatePastStates;
        end
        %---------------------------------------------------- functions
        function evolve(obj)
            obj.state = obj.caRule;
            obj.updatePastStates;
        end
        function play(obj)
            disp('Press a key to stop the simulation')
            KEY_STOP = 0;
            function keyPress(~, ~);KEY_STOP=1;end
            figure(100)
            colormap parula
            set(gcf, 'KeyPressFcn', @keyPress,'units','normalized',...
                'position',[0,1,obj.dispWidth,obj.dispHeight],...
                'Name',['Rule Number: ',num2str(obj.rule)],...
                'NumberTitle','Off', 'ToolBar','None','MenuBar','None');
            set(gca,'position',[0 0 1 1],'units','normalized')
            while ~KEY_STOP
                imagesc(obj.pastStates)
                axis off
                box on
                caxis([0,1])
                drawnow
                obj.evolve;
            end
        end
    end %-------------------------------------------------------------*
    
    methods (Access = protected) %----------------------- PROTECTED METHODS
        %-------------------------------------- internal update methods
        function updateRuleArray(obj)
            obj.ruleArray = arrayfun(@str2num,dec2bin(obj.rule,8));
        end
        function updatePastStates(obj)
            obj.pastStates = [obj.pastStates;obj.state];
            obj.pastStates(1,:) = [];
        end
        %--------------------------------- the <3 of the CA, be careful
        function newState = caRule(obj)
            newState = obj.ruleArray(8-filter2([4,2,1],...
                padarray(obj.state,[0,1],'circular'),'valid'));
        end
    end %-------------------------------------------------------------*
end
