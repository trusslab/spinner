
#include "SVF-LLVM/LLVMUtil.h"
#include "Graphs/SVFG.h"
#include "WPA/Andersen.h"
#include "SVF-LLVM/SVFIRBuilder.h"
#include "Util/Options.h"
#include "Util/CallGraphBuilder.h"
#include "SVF-LLVM/CHGBuilder.h"
#include <stdio.h>
#include "llvm/IR/Function.h"
#include "llvm/IR/ValueSymbolTable.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include <iterator>
//#include "WPA/AndersenPWC.h"
#include "WPA/Steensgaard.h"
//#include "WPA/TypeAnalysis.h"
//#include "MTA/FSMPTA.h"
#include "WPA/VersionedFlowSensitive.h"

using namespace llvm;
using namespace std;
using namespace SVF;

static llvm::cl::opt<std::string> InputFilename(cl::Positional,
        llvm::cl::desc("<input bitcode>"), llvm::cl::init("-"));



int main(int argc, char ** argv)
{
    
    int arg_num = 0;
    char **arg_value = new char*[argc];
    std::vector<std::string> moduleNameVec; 

  
    LLVMUtil::processArguments(argc, argv, arg_num, arg_value, moduleNameVec);
    cl::ParseCommandLineOptions(arg_num, arg_value, "Kernel Static Analysis\n");
    
    /*
     if (Options::WriteAnder() == "ir_annotator")
    { 
        LLVMModuleSet::getLLVMModuleSet()->preProcessBCs(moduleNameVec);
    }
    */
	
/* 
    static LLVMContext Context;
    MemoryBufferRef file = *MemoryBuffer::getFile(argv[1]).get();
    Expected<std::unique_ptr<llvm::Module>> ModuleOb = llvm::parseBitcodeFile(file, Context);  
    errs() << toString(std::move(ModuleOb.takeError())) << "\n"; 
    	
    for (auto v:moduleNameVec){
	    cout<<v<<"\n";
    }
  */  

    //llvmms->preProcessBCs(moduleNameVec);
   
    //cout<<"Searching for memset..."<<"\n";
    //SVFModule* svfmodule = getSVFModule();
   
    
    
//	    auto &ms = ModuleOb.get().get()->getValueSymbolTable();
	  /*  for (auto it = ms.begin(), end = ms.end(); it!=end; ++it) {
		    cout<<it->second;
		    cout<<"heelo";
	    }
	    */
	/*
	auto &fl =mod.get().getFunctionList();
    	for (auto &function: fl) {
	    cout<<function.getName().str();
	}
	*/
    


    
    cout<<"creating svfModule..."<<"\n";
    SVFModule* svfModule = LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);
    /*
    for (auto fun : svfModule->getFunctionSet())
    {
	    cout<<fun->getName()<<"\n";
    }
    */

    /*
    for (auto symbol : svfModule->getGlobalSet())
    {
	cout<<symbol->getName()<<"\n";
	cout<<symbol->toString()<<"\n";
    }		
    */

    //cout<<svfModule->getSVFFunction("memset")->getName();
    
     
    cout<<"creating pointer assignment graph...";
    SVFIRBuilder builder(svfModule);
    SVFIR* pag = builder.build();
    

    /*
    CHGraph *chg = new CHGraph(pag->getModule());
    CHGBuilder cbd(chg);
    cbd.buildCHG();
    pag->setCHG(chg);
    chg->dump("chg_example_2");
    */

    
    //cout<<"generating callgraph.."; 
    
    
    //only direct calls
    /* 
    PTACallGraph * cg = new PTACallGraph();
    CallGraphBuilder bd(cg, pag->getICFG());   
    PTACallGraph * callgraph = bd.buildCallGraph(svfModule);
    */

    /* 
    Steensgaard* pa = Steensgaard::createSteensgaard(pag);
    PTACallGraph* callgraph = pa->getPTACallGraph();
    */

    PTACallGraph* callgraph = AndersenWaveDiff::createAndersenWaveDiff(pag)->getPTACallGraph();
    builder.updateCallGraph(callgraph);
    callgraph->dump("callgraph_linux_andersenwave_complete_69");
    //pag->dump("pag_example_2");
    //
    //
   
    cout<<"done!";
}

