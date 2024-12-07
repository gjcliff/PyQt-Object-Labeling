#pragma once

#include <QObject>
#include <QString>
#include <QImage>
#include <QRect>
#include <QDebug>
#include <QFile>

class ImageProcessor : public QObject {
    Q_OBJECT
public:
    explicit ImageProcessor(QObject *parent = nullptr); // Constructor
    ~ImageProcessor() override; // Destructor

    Q_INVOKABLE void loadImage(const QString &filePath);
    Q_INVOKABLE void saveCroppedImage(const QRect &rect, const QString &outputPath);

    QImage currentImage() const;

signals:
    void imageLoaded();

private:
    QImage m_image;
};
