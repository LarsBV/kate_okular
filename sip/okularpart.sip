%Module Okular.Part

%Import kparts/kpartsmod.sip
%Import QtCore/QtCoremod.sip
%Import QtGui/QtGuimod.sip

namespace Okular {

class Part : KParts::ReadWritePart
{
%TypeHeaderCode
#include "/home/lars/software/source/okular/part.h"
%End


public:
        Part(QWidget* parentWidget, QObject* parent, const QVariantList& args, KComponentData componentData);
        bool isWatchFileModeEnabled() const;
        void setWatchFileModeEnabled(bool enable);
//	QString getSourceReference(const QPoint p);
//	QWidget* pageView();		
};

};

