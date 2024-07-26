#include "llvm/ADT/SmallVector.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Type.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/Support/SourceMgr.h"
#include <iostream>

using namespace llvm;

int main(int argc, char **argv) {
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " <input.bc>\n";
    return 1;
  }

  LLVMContext context;
  SMDiagnostic error;

  // Parse the input .bc file
  std::unique_ptr<Module> module = parseIRFile(argv[1], error, context);
  if (!module) {
    error.print(argv[0], errs());
    return 1;
  }

  // Iterate through all functions in the module
  for (const Function &function : *module) {
    // Print the name of each function
    std::cout << "Function: " << function.getName().str() << "\n";
  }

  return 0;
}
