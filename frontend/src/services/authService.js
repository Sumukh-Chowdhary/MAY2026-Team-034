import users from '../data/users.json'

export function login(username,password){
    return users.find(user=>
        (user.email===username || user.registerNumber===username) && user.password===password
    )
}