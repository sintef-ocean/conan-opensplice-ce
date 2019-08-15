#include "Test_DCPS.hpp"

#include <dds/domain/DomainParticipant.hpp>
#include <dds/sub/DataReader.hpp>
#include <dds/pub/DataWriter.hpp>
#include <dds/pub/Publisher.hpp>
#include <dds/sub/Subscriber.hpp>
#include <dds/topic/Topic.hpp>


int main()
{
    auto dp = dds::domain::DomainParticipant(0);
    auto pub = dds::pub::Publisher(dp);
    auto sub = dds::sub::Subscriber(dp);
    auto topic = dds::topic::Topic<Test::Message>(dp, "hello");
    auto reader = dds::sub::DataReader<Test::Message>(sub, topic);
    auto writer = dds::pub::DataWriter<Test::Message>(pub, topic);
    const auto outMsg = Test::Message(123);
    writer << outMsg;
    const auto inMsg = reader.take().begin()->data();
    return inMsg.payload() == 123 ? 0 : 1;
}
