///
/// Copyright (C) 2025, PriyaBG313
///
/// Permission is hereby granted, free of charge, to any person obtaining a copy
/// of this software and associated documentation files (the "Software"), to deal
/// in the Software without restriction, including without limitation the rights
/// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
/// copies of the Software, and to permit persons to whom the Software is
/// furnished to do so, subject to the following conditions:
///
/// The above copyright notice and this permission notice shall be included in all
/// copies or substantial portions of the Software.
///
/// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
/// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
/// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
/// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
/// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
/// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
/// SOFTWARE.
///

#ifndef S2E_PLUGINS_DEADLOCKTIMER_H
#define S2E_PLUGINS_DEADLOCKTIMER_H

#include <s2e/Plugin.h>

#include <s2e/Plugins/Core/BaseInstructions.h>


namespace s2e {
namespace plugins {


enum S2E_DEADLOCKTIMER_COMMANDS {
    // TODO: customize list of commands here
    COMMAND_1
};

struct S2E_DEADLOCKTIMER_COMMAND {
    S2E_DEADLOCKTIMER_COMMANDS Command;
    union {
        // Command parameters go here
        uint64_t param;
    };
};



class DeadlockTimer : public Plugin, public IPluginInvoker {

    S2E_PLUGIN
public:
    DeadlockTimer(S2E *s2e) : Plugin(s2e) {
    }

    void initialize();
    void onTimer();
    void onTranslateInstruction(ExecutionSignal *signal, S2EExecutionState *state, TranslationBlock *tb, uint64_t pc);
    void onInstructionExecution(S2EExecutionState *state, uint64_t pc);

private:
    uint64_t m_address_start;

    uint64_t m_address_irqsave_lock;
    uint64_t m_address_irqrestore_unlock;

    uint64_t m_address_irq_lock;
    uint64_t m_address_irq_unlock;
    
    uint64_t m_address_bh_lock;
    uint64_t m_address_bh_unlock;

    uint64_t m_address_lock;
    uint64_t m_address_unlock;
    bool tracking;
    std::unordered_map<uint64_t, pid_t> lockOwners;
    virtual void handleOpcodeInvocation(S2EExecutionState *state, uint64_t guestDataPtr, uint64_t guestDataSize);

};

} // namespace plugins
} // namespace s2e

#endif // S2E_PLUGINS_DEADLOCKTIMER_H
