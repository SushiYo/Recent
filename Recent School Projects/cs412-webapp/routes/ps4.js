const express = require('express');
const router = express.Router();
const request = require('request');
const fetch = require('node-fetch');
const value = require('./config');

router.all('/', function(req, res, next) {
    res.set("Access-Control-Allow-Origin", "*");
    res.set("Access-Control-Allow-Headers", "X-Requested-With");
    next()
});
const doReq_async = async(inputValue)=> {
    let returnValueRaw = await fetch(value.valUrl1+inputValue+'?api_key='+value.options.headers.Api)

    let returnValue = await returnValueRaw.json();

    const level = returnValue.summonerLevel;
    const name = returnValue.name;
    const icon = returnValue.profileIconId;
    return [level, name, value.imageUrl+icon+'.png']

}


const doReq_promise = function(name_val){
    return new Promise(function(resolve,reject){
        const options = {
            'method': value.options.method,
            'url': value.options.url+name_val,
            'headers': {
                'X-Riot-Token': value.options.headers.Api
            }
        };
        request(options, function(error, response, body){
            if(error)
                throw new Error(error)
            else{
                const theBody = JSON.parse(body);
                resolve(theBody);
            }

        })
    })
}

const doReq_call = function (callback, name_val){
    const options = {
        'method': value.options.method,
        'url': value.options.url+name_val,
        'headers': {
            'X-Riot-Token': value.options.headers.Api
        }
    };
    request(options, function (error, response, body) {

        if (error){
            callback("ERROR WITH SEARCH");
            throw new Error(error);

        }
        else{
            const theBody = JSON.parse(body);
            const level = theBody.summonerLevel;
            const name = theBody.name;
            const icon = theBody.profileIconId;
            console.log(level, name, icon)

            callback([level,name,value.imageUrl+icon+'.png',
        ])

        }
    });

}

const x = function (val){

    res.render('ps4', {lol: false, sval: val});

}

/* GET home page. */
router.get('/', function(req, res, next) {
    res.render("ps4", { lol: true});

});

router.post('/callback', function(req, res, next) {
    let test = doReq_call((test)=> res.render('ps4', {lol: false, sval: test}), req.body.search);

});

router.post('/promise', function(req, res, next){
    doReq_promise()
        .then(function(body){
            //let response = JSON.parse(body).summonerLevel;
            doReq_promise(req.body.search)
                .then(body => {
                    console.log(body);
                    const level = body.summonerLevel;
                    const name = body.name;
                    const icon = body.profileIconId;
                    res.render('ps4', {lol: false, sval: [level, name, value.imageUrl+icon+'.png']});
                })
        })
        .catch(err => console.log('in the catch', err))
});

router.post('/async', function(req, res, next){
    doReq_async(req.body.search)
        .then(
            returnValue =>{
                res.render('ps4', {lol: false, sval: returnValue});

            },
            error =>{
                console.log(`Rejected with ${error}`)
                res.render('ps4', {lol: false, sval: "ERROR WITH SEARCH"});
            }
        )
});
router.get('/asyncVal:vov',function(req, res, next){

    doReq_async(req.params.vov)
        .then(
            returnValue =>{

                res.send( {lol: false, sval: returnValue});

            },
            error =>{
                console.log(`Rejected with ${error}`)
                res.send({lol: false, sval: "ERROR WITH SEARCH"});
            }
        )
});

router.get('/promisesVal:vov', function(req, res, next){

    res.set("Access-Control-Allow-Origin", "*");
    res.set("Access-Control-Allow-Headers", "X-Requested-With");
    doReq_promise()
        .then(function(body){
            //let response = JSON.parse(body).summonerLevel;
            doReq_promise(req.params.vov)
                .then(body => {
                    console.log(req.body);
                    const level = body.summonerLevel;
                    const name = body.name;
                    const icon = body.profileIconId;

                    res.send({lol: false, sval: [level, name, value.imageUrl+icon+'.png']});
                })
        })
        .catch(err => console.log('in the catch', err))
});
router.get('/callbackVal/:vov', function(req, res, next) {
    res.set("Access-Control-Allow-Origin", "*");
    res.set("Access-Control-Allow-Headers", "X-Requested-With");
    let test = doReq_call((test)=> res.send({lol: false, sval: test}), req.params.vov);

});

router.options('/', function(req,res,next){
    res.set("Access-Control-Allow-Origin", "*");
    res.set("Access-Control-Allow-Headers", "X-Requested-With");
    res.send({})
})
module.exports = router;
