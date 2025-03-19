// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract StudentVerification {
    struct Student {
        string name;
        string instituteCode;
        string uhi;
        bool isRegistered;
    }

    mapping(string => Student) private students;  // Mapping UHI to Student details

    event StudentRegistered(string indexed uhi, string name);
    event StudentVerified(string indexed uhi, string name, bool isValid);

    // Function to register a student
    function registerStudent(string memory _name, string memory _instituteCode, string memory _uhi) public {
        require(!students[_uhi].isRegistered, "Student already registered.");  // Only check by UHI

        students[_uhi] = Student(_name, _instituteCode, _uhi, true);
        emit StudentRegistered(_uhi, _name);
    }

    // Function to verify if a student is registered (both name and UHI must match)
    function verifyStudent(string memory _name, string memory _uhi) public view returns (bool) {
    return students[_uhi].isRegistered && keccak256(abi.encodePacked(students[_uhi].name)) == keccak256(abi.encodePacked(_name));
}
}
