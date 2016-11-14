React = require 'react'
ReactDOM = require 'react-dom'
somata = require './somata-stream'
KefirBus = require 'kefir-bus'

scores$ = KefirBus()
played$ = KefirBus()

Word = React.createClass
    onClick: ->
        somata.remote 'election2016', 'word', @props.index
            .onValue ({scores, played}) ->
                scores$.emit scores
                played$.emit played

    render: ->
        <a onClick=@onClick className='word'>{@props.word}</a>

Words = React.createClass
    getInitialState: ->
        words: []

    componentDidMount: ->
        somata.remote 'election2016', 'words'
            .onValue @setWords

    setWords: (words) ->
        @setState {words}

    render: ->
        <div className='words'>
            {@state.words.map (word, wi) ->
                <Word word=word index=wi key=wi />
            }
        </div>

RecentWords = React.createClass
    getInitialState: ->
        played: []

    componentDidMount: ->
        played$.onValue @setPlayed

    setPlayed: (played) -> @setState {played}

    undo: ->
        somata.remote 'election2016', 'undo'
            .onValue ({scores, played}) ->
                scores$.emit scores
                played$.emit played

    render: ->
        n = 20
        most_recent = @state.played.slice(-1 * n).reverse()

        <div className='recent-words'>
            <h3>Last {n} words</h3>
            <button onClick=@undo>Undo</button>
            {most_recent.map (word, wi) ->
                <li className='recent-word' key=wi>{word}</li>
            }
        </div>

Player = React.createClass
    render: ->
        <div className='player'>
            <span className='score'>{@props.score}</span>
            <span className='name'>{@props.name}</span>
            <span className='next'>{@props.next}</span>
        </div>

Scores = React.createClass
    getInitialState: ->
        teams: []

    componentDidMount: ->
        scores$
            .onValue @setTeams

    setTeams: (teams) ->
        @setState {teams}

    render: ->
        <div className='teams'>
            {Object.keys(@state.teams).map (team_name) =>
                team = @state.teams[team_name]
                <Team team=team team_name=team_name key=team_name />
            }
        </div>

add = (a, b) -> a + b
sum = (l) -> l.reduce add, 0

Team = React.createClass
    render: ->
        total = sum Object.keys(@props.team).map (player_name) => @props.team[player_name].score
        team_name = if @props.team_name == 'A' then 'Stars' else 'Stripes'
        <div className={'team team-' + @props.team_name}>
            <div className='title'>
                <h1>{team_name}</h1>
                <h2>{total}</h2>
            </div>
            {Object.keys(@props.team).map (player_name) =>
                player = @props.team[player_name]
                console.log 'player', player
                <Player name=player_name score=player.score next=player.next />
            }
        </div>

Swapper = React.createClass
    getInitialState: ->
        names1: []
        names2: []
        name1: null
        name2: null

    componentDidMount: ->
        scores$
            .onValue @setTeams

    setTeams: (teams) ->
        console.log 'teams', teams
        @setState
            names1: Object.keys teams.A
            names2: Object.keys teams.B

    onChoose: (t) -> (e) =>
        name = e.target.value
        if t == 'A'
            @setState {name1: name}
        else
            @setState {name2: name}

    renderNames: (t) ->
        names = if t == 'A' then @state.names1 else @state.names2
        <select onChange=@onChoose(t)>
            <option value=null>Choose player</option>
            {names.map (name) ->
                <option value=name key=name>{name}</option>
            }
        </select>

    doSwap: ->
        somata.remote 'election2016', 'swap', @state.name1, @state.name2
            .onValue (scores) -> scores$.emit scores

    render: ->
        <div className='swapper'>
            Swap: 
            {@renderNames('A')}
            {@renderNames('B')}
            <button onClick=@doSwap>Swap</button>
        </div>

App = React.createClass
    componentDidMount: ->
        somata.remote 'election2016', 'scores'
            .onValue (scores) -> scores$.emit scores
        somata.remote 'election2016', 'played'
            .onValue (played) -> played$.emit played

    render: ->
        <div className='main'>
            <Words />
            <div className='middle'>
                <Scores />
                <Swapper />
            </div>
            <RecentWords />
        </div>

ReactDOM.render <App />, document.getElementById 'app'
