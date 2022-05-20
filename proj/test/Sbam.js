var Sbam = artifacts.require("./Sbam.sol");

contract("Sbms async", (accounts, msg) =>
{
  it("test register" , async ()  => {
    const instance = await Sbam.new()
    const ret = await instance.registerUser.call("yes")
    //console.error("errorr is" + ret)
    assert.equal(ret.toString(), "true", "expect ret to equal true")
    
  })

  it("test same register twice" , async () => {
    const instance = await Sbam.new()
    await instance.registerUser("user")
    const ret = await instance.registerUser.call("user")
    //console.error("errorr is" + ret)
    assert.equal(ret.toString(), "false", "expect ret to equal false")
    
  })

  it("test new register" , async () => {
    const instance = await Sbam.new({from: accounts[0]})
    //instance.deposit(accounts[0], {from: someAccount, value: someValueInWei});
    //await instance.register(msg.sender)
    await instance.registerUser(accounts[0])
    //console.error("errorr is" + ret)
    //assert.equal(ret1.toString(), "true", "expect ret1 to equal true")

    const ret2 = await instance.registerUser.call(accounts[0])
    //console.error("errorr is" + ret)
    assert.equal(ret2.toString(), "false", "expect ret2 to equal false")
    
  })
})