const StudentVerification = artifacts.require("StudentVerification");

module.exports = function (deployer) {
    deployer.deploy(StudentVerification);
};
